/* eslint-disable @typescript-eslint/no-unused-vars */
import { Row, Card, Form, Space, Typography } from 'antd'
import { Layout } from '../../components/layout'
import { CustomInput } from '../../components/custom-input'
import { PasswordInput } from '../../components/password-input'
import { CustomButton } from '../../components/custom-button'
import { Link, useNavigate } from 'react-router-dom'
import { Paths } from '../../paths'
import { UserData, useLoginMutation } from '../../app/services/auth'
import { isErrorWithMessage } from '../../utils/is-error-with-message'
import { useState } from 'react'
import { ErrorMessage } from '../../components/error-message'

export const Login = () => {
  const navigate = useNavigate();
  const [loginUser, loginUserResult] = useLoginMutation();
  const [error, setError] = useState('');

  const login = async (data: UserData) => {
    try {
      await loginUser(data).unwrap();
      navigate("/")
    } catch (err) {
      console.log(err);

      const maybeError = isErrorWithMessage(err);

      if (maybeError) {
        setError(err.data.message);
      } else {
        setError('Unknown error')
      }
    }
  }

  return (
    <Layout>
      <Row align="middle" justify="center">
        <Card title="Log in" style={{ width: "30rem" }}>
          <Form onFinish={login}>
            <CustomInput name={'email'} placeholder={'Enter your email'} type="email"></CustomInput>
            <PasswordInput name={'password'} placeholder={'Enter your password'}></PasswordInput>
            <CustomButton type="primary" htmlType='submit'>Log in</CustomButton>
          </Form>
          <Space direction='vertical' size='large'>
            <Typography.Text>
              No account? <Link to={Paths.register}>Sign in</Link>
            </Typography.Text>
            <ErrorMessage message={error} />
          </Space>
        </Card>
      </Row>
    </Layout>
  )
}
